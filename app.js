/**
 * 主应用逻辑 - 静态网页版
 * 整合UI交互和数据处理器
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM元素
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const triggerFileInput = document.getElementById('triggerFileInput');
  const sampleLink = document.getElementById('sampleLink');
  const fileQueueEl = document.getElementById('fileQueue');
  const processBtn = document.getElementById('actionProcess');
  const clearBtn = document.getElementById('actionClear');
  const resultPanel = document.getElementById('resultPanel');
  const sessionSummary = document.getElementById('sessionSummary');
  const fileResults = document.getElementById('fileResults');
  const resultBadge = document.getElementById('resultBadge');

  // Toast容器
  const toastHost = document.createElement('div');
  toastHost.className = 'toast-host';
  document.body.appendChild(toastHost);

  // 应用状态
  const state = {
    files: [],
    processing: false,
    counter: 0,
    maxFileSize: 10 * 1024 * 1024, // 静态版本推荐10MB
    maxFileCount: 5, // 降低为5个文件
    processor: new DataProcessor()
  };

  // 工具函数：从文件名提取周序号
  function extractWeekNumber(filename) {
    const patterns = [
      /第\s*(\d+)\s*周/i,
      /周\s*(\d+)/i,
      /W(\d+)/i,
      /week\s*(\d+)/i,
      /_W(\d+)_/i,
      /-W(\d+)-/i
    ];

    for (const pattern of patterns) {
      const match = filename.match(pattern);
      if (match && match[1]) {
        const weekNum = parseInt(match[1]);
        if (weekNum >= 1 && weekNum <= 53) {
          return weekNum;
        }
      }
    }
    return null;
  }

  // 工具函数：格式化文件大小
  function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) return '—';
    const units = ['B', 'KB', 'MB', 'GB'];
    const exp = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
    const value = bytes / Math.pow(1024, exp);
    return `${value.toFixed(exp === 0 ? 0 : 1)} ${units[exp]}`;
  }

  // 工具函数：显示Toast消息
  function showToast(message, variant = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast--${variant}`;
    toast.textContent = message;
    toastHost.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('is-leaving');
      setTimeout(() => toast.remove(), 320);
    }, 3200);
  }

  // 工具函数：设置结果徽章
  function setBadge(mode, text) {
    const badgeModes = ['badge--processing', 'badge--success', 'badge--error', 'badge--idle', 'badge--warning'];
    resultBadge.textContent = text;
    resultBadge.classList.remove(...badgeModes);

    switch (mode) {
      case 'processing':
        resultBadge.classList.add('badge--processing');
        break;
      case 'success':
        resultBadge.classList.add('badge--success');
        break;
      case 'warning':
        resultBadge.classList.add('badge--warning');
        break;
      case 'error':
        resultBadge.classList.add('badge--error');
        break;
      default:
        resultBadge.classList.add('badge--idle');
    }
  }

  // 工具函数：更新控件状态
  function updateControls() {
    const hasProcessable = state.files.some(file => file.status === 'queued');
    processBtn.disabled = state.processing || !hasProcessable;
    clearBtn.disabled = state.processing || state.files.length === 0;
    updateFileStats();
  }

  // 工具函数：更新文件统计
  function updateFileStats() {
    const fileStats = document.getElementById('fileStats');
    if (state.files.length === 0) {
      fileStats.innerHTML = '';
      return;
    }

    const totalSize = state.files.reduce((sum, entry) => sum + entry.file.size, 0);
    const validFiles = state.files.filter(entry => entry.status === 'queued').length;

    let statsHtml = `<div style="font-size: 13px; color: var(--text-muted);">`;
    statsHtml += `共 ${state.files.length} 个文件，总计 ${formatBytes(totalSize)}`;

    if (validFiles > 0) {
      statsHtml += `，<span style="color: var(--success);">${validFiles} 个可处理</span>`;
    }

    statsHtml += `</div>`;

    // 大小警告
    if (totalSize > 20 * 1024 * 1024) {
      statsHtml += `<div style="font-size: 12px; color: var(--warning); margin-top: 4px;">⚠️ 文件较大，浏览器处理可能较慢，建议使用服务器版本</div>`;
    }

    fileStats.innerHTML = statsHtml;
  }

  // 渲染文件队列
  function renderQueue() {
    fileQueueEl.innerHTML = '';
    if (state.files.length === 0) {
      fileQueueEl.classList.add('is-empty');
      fileQueueEl.textContent = '尚未选择文件';
      updateControls();
      return;
    }

    fileQueueEl.classList.remove('is-empty');

    const table = document.createElement('div');
    table.className = 'file-table';

    // 表头
    const header = document.createElement('div');
    header.className = 'file-table__header';
    const headerRow = document.createElement('div');
    headerRow.className = 'file-table__header-row';
    headerRow.innerHTML = `
      <div class="file-table__header-cell">上传文件</div>
      <div class="file-table__header-cell file-table__header-cell--center">格式</div>
      <div class="file-table__header-cell file-table__header-cell--right">大小</div>
      <div class="file-table__header-cell file-table__header-cell--center">状态</div>
      <div class="file-table__header-cell file-table__header-cell--center">周序号</div>
      <div class="file-table__header-cell file-table__header-cell--center">操作</div>
    `;
    header.appendChild(headerRow);
    table.appendChild(header);

    // 表体
    const tbody = document.createElement('div');
    tbody.className = 'file-table__body';

    state.files.forEach(entry => {
      const row = document.createElement('div');
      row.className = 'file-table__row';
      row.dataset.id = entry.id;

      // 文件名
      const nameCell = document.createElement('div');
      nameCell.className = 'file-table__cell';
      nameCell.innerHTML = `
        <div class="file-name">
          <span class="file-name__icon">📄</span>
          <span class="file-name__text" title="${entry.file.name}">${entry.file.name}</span>
        </div>
      `;

      // 格式
      const formatCell = document.createElement('div');
      formatCell.className = 'file-table__cell file-table__cell--center';
      formatCell.innerHTML = `<span class="file-format">${entry.file.name.slice(entry.file.name.lastIndexOf('.')).toLowerCase()}</span>`;

      // 大小
      const sizeCell = document.createElement('div');
      sizeCell.className = 'file-table__cell file-table__cell--right';
      sizeCell.innerHTML = `<span class="file-size">${formatBytes(entry.file.size)}</span>`;

      // 状态
      const statusCell = document.createElement('div');
      statusCell.className = 'file-table__cell file-table__cell--center';
      const statusMap = {
        queued: '待处理',
        processing: '处理中',
        success: '完成',
        error: '失败'
      };
      const statusClass = `status-pill status-pill--${entry.status}`;
      statusCell.innerHTML = `<span class="${statusClass}">${statusMap[entry.status] || '待处理'}</span>`;

      // 周序号
      const weekCell = document.createElement('div');
      weekCell.className = 'file-table__cell file-table__cell--center';
      const weekInput = document.createElement('input');
      weekInput.type = 'number';
      weekInput.className = 'week-number-input';
      weekInput.min = '1';
      weekInput.max = '53';
      weekInput.placeholder = '1-53';
      weekInput.value = entry.weekNumber || '';
      weekInput.disabled = state.processing;
      weekInput.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        if (value >= 1 && value <= 53) {
          entry.weekNumber = value;
        } else {
          entry.weekNumber = null;
        }
        updateControls();
      });

      const weekWrapper = document.createElement('div');
      weekWrapper.className = 'week-input-wrapper';
      weekWrapper.appendChild(weekInput);

      if (entry.autoDetected) {
        const hint = document.createElement('span');
        hint.className = 'week-auto-hint';
        hint.textContent = '✓';
        hint.title = '已自动识别';
        weekWrapper.appendChild(hint);
      }

      weekCell.appendChild(weekWrapper);

      // 操作
      const actionsCell = document.createElement('div');
      actionsCell.className = 'file-table__cell file-table__cell--center';
      if (!state.processing && entry.status !== 'processing') {
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn-remove';
        removeBtn.textContent = '×';
        removeBtn.setAttribute('data-remove-id', entry.id);
        actionsCell.appendChild(removeBtn);
      }

      row.appendChild(nameCell);
      row.appendChild(formatCell);
      row.appendChild(sizeCell);
      row.appendChild(statusCell);
      row.appendChild(weekCell);
      row.appendChild(actionsCell);

      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    fileQueueEl.appendChild(table);

    updateControls();
  }

  // 添加文件
  function addFiles(fileList) {
    const incoming = Array.from(fileList);
    if (!incoming.length) return;

    let validFiles = [];
    let sizeErrors = [];
    let formatErrors = [];

    incoming.forEach(file => {
      if (file.size > state.maxFileSize) {
        sizeErrors.push({ name: file.name, size: file.size });
        return;
      }

      if (!/\.(xlsx|xls)$/i.test(file.name)) {
        formatErrors.push(file.name);
        return;
      }

      const duplicate = state.files.find(entry =>
        entry.file.name === file.name && entry.file.size === file.size
      );
      if (duplicate) return;

      validFiles.push(file);
    });

    if (sizeErrors.length > 0) {
      showToast(`文件过大: ${sizeErrors[0].name} (${formatBytes(sizeErrors[0].size)})，推荐 ≤ 10MB`, 'error');
    }

    if (formatErrors.length > 0) {
      showToast(`格式不支持: ${formatErrors.slice(0, 2).join(', ')}`, 'warning');
    }

    // 检查文件数量
    const totalFiles = state.files.length + validFiles.length;
    if (totalFiles > state.maxFileCount) {
      const canAdd = Math.max(0, state.maxFileCount - state.files.length);
      validFiles = validFiles.slice(0, canAdd);
      showToast(`最多允许 ${state.maxFileCount} 个文件`, 'warning');
    }

    // 添加有效文件
    validFiles.forEach(file => {
      const detectedWeek = extractWeekNumber(file.name);

      const entry = {
        id: `file-${++state.counter}`,
        file,
        status: 'queued',
        weekNumber: detectedWeek,
        autoDetected: detectedWeek !== null
      };

      if (detectedWeek) {
        showToast(`已自动识别周序号: 第${detectedWeek}周 - ${file.name}`, 'success');
      }

      state.files.push(entry);
    });

    renderQueue();
  }

  // 移除文件
  function removeFile(id) {
    state.files = state.files.filter(entry => entry.id !== id);
    renderQueue();
  }

  // 清空文件
  function clearFiles() {
    state.files = [];
    renderQueue();
    sessionSummary.innerHTML = '';
    fileResults.innerHTML = '';
    setBadge('idle', '等待上传');
    resultPanel.classList.add('is-hidden');
  }

  // 验证上传前
  function validateBeforeUpload() {
    const processable = state.files.filter(file => file.status === 'queued');

    if (!processable.length) {
      showToast('请先添加至少一个 Excel 文件', 'info');
      return false;
    }

    const missingWeek = processable.filter(entry => !entry.weekNumber || entry.weekNumber < 1 || entry.weekNumber > 53);
    if (missingWeek.length > 0) {
      showToast(`请为所有文件设置有效的周序号(1-53)。缺失周序号的文件: ${missingWeek.length} 个`, 'warning');
      return false;
    }

    return true;
  }

  // 处理文件
  async function processFiles() {
    if (!validateBeforeUpload()) return;

    const processable = state.files.filter(file => file.status === 'queued');

    state.processing = true;
    processable.forEach(file => {
      file.status = 'processing';
    });
    renderQueue();

    resultPanel.classList.remove('is-hidden');
    setBadge('processing', '处理中');

    sessionSummary.innerHTML = '<div class="summary-card"><div class="summary-card__value">⏱</div><div class="summary-card__label">正在处理</div></div>';

    const allResults = [];
    let successCount = 0;
    let failCount = 0;

    for (const entry of processable) {
      try {
        console.log(`处理文件: ${entry.file.name}`);

        const result = await state.processor.processExcelFile(entry.file, entry.weekNumber);

        if (result.success) {
          entry.status = 'success';
          entry.result = result;
          successCount++;
          allResults.push({
            filename: entry.file.name,
            weekNumber: entry.weekNumber,
            data: result.data,
            years: result.years,
            totalRows: result.totalRows
          });
        } else {
          entry.status = 'error';
          entry.error = result.error;
          failCount++;
        }
      } catch (error) {
        console.error(`处理文件失败: ${entry.file.name}`, error);
        entry.status = 'error';
        entry.error = error.message;
        failCount++;
      }

      renderQueue();
    }

    // 显示结果
    renderResults(allResults, successCount, failCount);

    state.processing = false;
    updateControls();

    if (failCount === 0) {
      setBadge('success', '全部完成');
      showToast('全部文件处理完成！', 'success');
    } else if (successCount > 0) {
      setBadge('warning', '部分完成');
      showToast(`处理完成，${successCount} 个成功，${failCount} 个失败`, 'warning');
    } else {
      setBadge('error', '处理失败');
      showToast('处理失败，请检查文件格式', 'error');
    }
  }

  // 渲染结果
  function renderResults(results, successCount, failCount) {
    // 显示摘要
    sessionSummary.innerHTML = `
      <div class="summary-card"><div class="summary-card__value">${results.length}</div><div class="summary-card__label">处理文件</div></div>
      <div class="summary-card"><div class="summary-card__value">${successCount}</div><div class="summary-card__label">成功</div></div>
      <div class="summary-card"><div class="summary-card__value">${failCount}</div><div class="summary-card__label">失败</div></div>
    `;

    // 显示每个文件的结果
    fileResults.innerHTML = '';
    results.forEach(result => {
      const card = document.createElement('article');
      card.className = 'result-card';

      card.innerHTML = `
        <div class="result-card__header">
          <h3 class="result-card__title">${result.filename}</h3>
          <span class="status-pill status-pill--success">完成</span>
        </div>
        <div class="result-card__meta">
          <span class="meta-chip">年度 · ${result.years.join(', ')}</span>
          <span class="meta-chip">周次 · 第 ${String(result.weekNumber).padStart(2, '0')} 周</span>
          <span class="meta-chip">总行数 · ${result.totalRows}</span>
        </div>
      `;

      // 添加下载链接
      const outputList = document.createElement('div');
      outputList.className = 'output-list';

      result.years.forEach(year => {
        const yearData = result.data[year];
        const filename = state.processor.generateFilename(year, result.weekNumber);
        const csvContent = state.processor.dataToCSV(yearData);

        const link = document.createElement('a');
        link.className = 'output-link';
        link.href = '#';
        link.textContent = filename;
        link.innerHTML += `<span class="output-meta">${yearData.length} 行</span>`;

        link.addEventListener('click', (e) => {
          e.preventDefault();
          downloadCSV(csvContent, filename);
          showToast(`已下载: ${filename}`, 'success');
        });

        outputList.appendChild(link);
      });

      card.appendChild(outputList);

      // 打包下载按钮
      if (result.years.length > 1) {
        const footer = document.createElement('div');
        footer.className = 'result-card__footer';

        const zipBtn = document.createElement('button');
        zipBtn.className = 'btn btn--ghost';
        zipBtn.textContent = `打包下载 (${result.years.length} 个文件)`;
        zipBtn.addEventListener('click', () => downloadAllAsZip(result));

        footer.appendChild(zipBtn);
        card.appendChild(footer);
      }

      fileResults.appendChild(card);
    });
  }

  // 下载CSV文件
  function downloadCSV(content, filename) {
    const blob = new Blob(['\ufeff' + content], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, filename);
  }

  // 打包下载ZIP
  async function downloadAllAsZip(result) {
    const zip = new JSZip();

    result.years.forEach(year => {
      const yearData = result.data[year];
      const filename = state.processor.generateFilename(year, result.weekNumber);
      const csvContent = state.processor.dataToCSV(yearData);

      zip.file(filename, '\ufeff' + csvContent);
    });

    const blob = await zip.generateAsync({ type: 'blob' });
    const zipFilename = `保单第${String(result.weekNumber).padStart(2, '0')}周变动成本明细表.zip`;
    saveAs(blob, zipFilename);

    showToast(`已打包下载: ${zipFilename}`, 'success');
  }

  // 事件绑定
  triggerFileInput.addEventListener('click', () => fileInput.click());

  sampleLink.addEventListener('click', () => {
    showToast('请参阅项目根目录下的《处理规范.md》了解字段说明。', 'info');
  });

  fileInput.addEventListener('change', event => {
    addFiles(event.target.files);
    fileInput.value = '';
  });

  dropZone.addEventListener('dragover', event => {
    event.preventDefault();
    dropZone.classList.add('is-dragover');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('is-dragover');
  });

  dropZone.addEventListener('drop', event => {
    event.preventDefault();
    dropZone.classList.remove('is-dragover');
    addFiles(event.dataTransfer.files);
  });

  fileQueueEl.addEventListener('click', event => {
    if (event.target.matches('[data-remove-id]')) {
      const id = event.target.getAttribute('data-remove-id');
      removeFile(id);
    }
  });

  clearBtn.addEventListener('click', () => {
    if (state.files.length === 0) return;
    clearFiles();
    showToast('已清空文件队列', 'info');
  });

  processBtn.addEventListener('click', () => {
    if (!state.processing) {
      processFiles();
    }
  });

  // 初始化
  setBadge('idle', '等待上传');
  updateControls();
  renderQueue();
});
