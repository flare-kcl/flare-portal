/**
 * fileInput
 *
 * Displays the selected file's filename on file inputs
 */
const fileInput = () => {
    const defaultText = 'Choose file...';
    return {
        text: defaultText,
        handleChange(ev) {
            this.text = ev.target.files[0]?.name || defaultText;
        },
    };
};

export default fileInput;
