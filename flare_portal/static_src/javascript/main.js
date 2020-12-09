import 'alpinejs';
import '../sass/main.scss';

import { Sortable } from '@shopify/draggable';

// eslint-disable-next-line no-unused-vars
window.require(['jquery', 'selectize'], ($, selectize) => {
    $(document).ready(() => {
        $('[data-selectize]').selectize({});
    });
});

window.draggable = function draggable($el) {
    // eslint-disable-next-line no-new
    new Sortable($el, { draggable: 'li' });
};
