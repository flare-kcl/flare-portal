import 'alpinejs';
import '../sass/main.scss';

// eslint-disable-next-line no-unused-vars
window.require(['jquery', 'selectize'], ($, selectize) => {
    $(document).ready(() => {
        $('[data-selectize]').selectize({});
    });
});
