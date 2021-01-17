import 'alpinejs';
import '../sass/main.scss';
import Cookies from 'js-cookie';

import { Sortable } from '@shopify/draggable';

// Enable selectize for select fields
// eslint-disable-next-line no-unused-vars
window.require(['jquery', 'selectize'], ($, selectize) => {
    $(document).ready(() => {
        $('[data-selectize]').selectize({ allowEmptyOption: true });
    });
});

/**
 * moduleList
 *
 * Allows the portal users to reorder the modules on an experiment
 */
window.moduleList = () => {
    return {
        message: '',
        messageType: 'success',
        messageTimeout: null,
        draggable() {
            const $el = this.$refs.modules;
            const sortable = new Sortable($el, {
                draggable: 'tr',
                handle: 'i.fe-menu',
            });

            sortable.on('sortable:stop', async () => {
                // Get the module order based on the DOM order
                const moduleOrder = Array.from($el.children)
                    .filter(
                        // Only include elements that weren't moved plus the element
                        // that was moved to a new position
                        ($moduleEl) =>
                            !$moduleEl.className.includes('draggable') ||
                            $moduleEl.classList.contains('draggable--over'),
                    )
                    .map(($moduleEl) => $moduleEl.dataset.moduleId);

                // Update the module sort order on the server
                const url = `${document.location.href}sort-modules/`;

                const postData = moduleOrder.reduce((acc, moduleId, index) => {
                    acc[moduleId] = index;
                    return acc;
                }, {});

                const resp = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': Cookies.get('csrftoken'),
                    },
                    body: JSON.stringify(postData),
                });

                const respData = await resp.json();

                // Display message
                this.message = respData.message;
                this.messageType = resp.status === 200 ? 'success' : 'error';

                // Clear out previous timeout if it exists
                if (this.messageTimeout) {
                    clearTimeout(this.messageTimeout);
                }

                // Hide success message after 5 seconds
                this.messageTimeout = setTimeout(() => {
                    this.message = '';
                }, 5000);
            });
        },
    };
};

/**
 * fileInput
 *
 * Displays the selected file's filename on file inputs
 */
window.fileInput = () => {
    const defaultText = 'Choose file...';
    return {
        text: defaultText,
        handleChange(ev) {
            this.text = ev.target.files[0]?.name || defaultText;
        },
    };
};
