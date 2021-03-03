import 'alpinejs';
import SimpleMDE from 'simplemde';
import '../sass/main.scss';
import 'simplemde/dist/simplemde.min.css';

import fileInput from './alpine_components/fileInput';
import moduleList from './alpine_components/moduleList';

// Enable selectize for select fields
// eslint-disable-next-line no-unused-vars
window.require(['jquery', 'selectize'], ($, selectize) => {
    $(document).ready(() => {
        $('[data-selectize]').selectize({ allowEmptyOption: true });
    });
});

// Initialise any markdown editors
document.querySelectorAll('[data-markdown-editor]').forEach((element) => {
    // Attach editor instance to TextArea element
    const editor = new SimpleMDE({
        element,
        forceSync: true,
        allowAtxHeaderWithoutSpace: true,
        spellChecker: true,
    });
});

// Expose Alpine components
window.moduleList = moduleList;
window.fileInput = fileInput;
