document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // Check localStorage
    const savedTheme = localStorage.getItem('theme') || 'dark';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateGridTheme(savedTheme);
    themeToggle.textContent = savedTheme === 'dark' ? '☀' : '🌙';

    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        themeToggle.textContent = newTheme === 'dark' ? '☀' : '🌙';
        
        updateGridTheme(newTheme);
    });
});

function updateGridTheme(theme) {
    const gridEl = document.getElementById('myGrid');
    if (gridEl) {
        if (theme === 'dark') {
            gridEl.classList.remove('ag-theme-alpine');
            gridEl.classList.add('ag-theme-alpine-dark');
        } else {
            gridEl.classList.remove('ag-theme-alpine-dark');
            gridEl.classList.add('ag-theme-alpine');
        }
    }
}
