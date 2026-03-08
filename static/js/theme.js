class ThemeManager {
    constructor() {
        this.currentTheme = this.loadTheme();
        this.init();
    }

    init() {
        // Apply saved theme
        this.applyTheme(this.currentTheme);
        
        // Setup theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    loadTheme() {
        // Load theme from localStorage, default to dark
        const savedTheme = localStorage.getItem('theme');
        return savedTheme || 'dark';
    }

    toggleTheme() {
        // Switch between dark and light
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(this.currentTheme);
        
        // Save to localStorage
        localStorage.setItem('theme', this.currentTheme);
    }

    applyTheme(theme) {
        // Set data-theme attribute on document
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update toggle button icon
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }
}
