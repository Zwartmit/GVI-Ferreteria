function changeFontSize(size) {
    console.log('Changing font size to:', size);
    const body = document.body;
    body.classList.remove('font-small', 'font-medium', 'font-large');
    
    if (size === 'small') {
        body.classList.add('font-small');
    } else if (size === 'medium') {
        body.classList.add('font-medium');
    } else if (size === 'large') {
        body.classList.add('font-large');
    }
}

document.addEventListener('DOMContentLoaded', function() {
});
