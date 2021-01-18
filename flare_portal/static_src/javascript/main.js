import 'alpinejs';
import '../sass/main.scss';

import fileInput from './alpine_components/fileInput';
import moduleList from './alpine_components/moduleList';

// Enable selectize for select fields
// eslint-disable-next-line no-unused-vars
window.require(['jquery', 'selectize'], ($, selectize) => {
    $(document).ready(() => {
        $('[data-selectize]').selectize({ allowEmptyOption: true });
    });
});

// Expose Alpine components
window.moduleList = moduleList;
window.fileInput = fileInput;
