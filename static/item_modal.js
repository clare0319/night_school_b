(function () {
    const style = document.createElement('style');
    style.textContent = `
        .choices {
            pointer-events: none;
            position: relative;
            z-index: 3;
        }
        .choices a,
        .choices button {
            pointer-events: auto;
        }
        .bag-button-container {
            position: relative;
            z-index: 4;
        }
        .dialog-box {
            position: relative;
            z-index: 2;
        }
        body::before {
            z-index: 0;
        }
    `;
    if (document.head) {
        document.head.appendChild(style);
    }

    function createOverlay() {
        if (document.getElementById('item-modal-overlay')) {
            return document.getElementById('item-modal-overlay');
        }

        const overlay = document.createElement('div');
        overlay.id = 'item-modal-overlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.75)';
        overlay.style.zIndex = '9999';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.padding = '20px';
        overlay.style.boxSizing = 'border-box';

        const panel = document.createElement('div');
        panel.id = 'item-modal-panel';
        panel.style.width = '100%';
        panel.style.maxWidth = '800px';
        panel.style.maxHeight = '90vh';
        panel.style.overflowY = 'auto';
        panel.style.borderRadius = '20px';
        panel.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.35)';
        panel.style.position = 'relative';

        overlay.appendChild(panel);
        document.body.appendChild(overlay);

        overlay.addEventListener('click', function (event) {
            if (event.target === overlay) {
                closeItemModal();
            }
        });

        return overlay;
    }

    function bindModalLinks(panel) {
        if (!panel) {
            return;
        }

        panel.querySelectorAll('[data-item-link]').forEach(function (link) {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                const itemName = this.getAttribute('data-item-name');
                if (itemName) {
                    openItemDetailModal(itemName);
                }
            });
        });
    }

    function renderModalContent(url) {
        const overlay = createOverlay();
        const panel = document.getElementById('item-modal-panel');
        panel.innerHTML = '<div style="padding: 24px; color: white; font-family: sans-serif;">불러오는 중...</div>';

        fetch(url)
            .then(function (response) {
                return response.text();
            })
            .then(function (html) {
                panel.innerHTML = html;
                bindModalLinks(panel);
            })
            .catch(function () {
                panel.innerHTML = '<div style="padding: 24px; color: white; font-family: sans-serif;">아이템 창을 불러오지 못했습니다.</div>';
            });

        return overlay;
    }

    function openItemModal() {
        renderModalContent('/bag?modal=1');
    }

    function openItemDetailModal(itemName) {
        const encodedName = encodeURIComponent(itemName);
        renderModalContent('/item_detail/' + encodedName + '?modal=1');
    }

    function closeItemModal() {
        const overlay = document.getElementById('item-modal-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    window.openItemModal = openItemModal;
    window.openItemDetailModal = openItemDetailModal;
    window.closeItemModal = closeItemModal;

    document.addEventListener('click', function (event) {
        const button = event.target.closest('button');
        if (!button) {
            return;
        }

        if ((button.textContent || '').trim() === '아이템') {
            event.preventDefault();
            event.stopPropagation();
            openItemModal();
        }
    });
})();
