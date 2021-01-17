import Cookies from 'js-cookie';

import debounce from 'lodash/debounce';

import { Sortable } from '@shopify/draggable';

/**
 * moduleList
 *
 * Allows portal users to reorder the modules on an experiment
 */
const moduleList = () => {
    return {
        showMessage: false,
        message: '',
        messageType: 'success',
        messageTimeout: null,
        draggable() {
            const $el = this.$refs.modules;
            const sortable = new Sortable($el, {
                draggable: 'tr',
                handle: 'i.fe-menu',
            });

            const saveSorting = async () => {
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

                // Display Saving... message
                this.message = 'Saving...';
                this.messageType = 'saving';
                this.showMessage = true;

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
                    this.showMessage = false;
                }, 5000);
            };

            sortable.on('sortable:stop', debounce(saveSorting, 1000));
        },
    };
};

export default moduleList;
