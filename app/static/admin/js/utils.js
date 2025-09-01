/**
 * Utility functions
 */
const Utils = {
    /**
     * Mostra un toast di notifica
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} fixed bottom-4 right-4 z-50 max-w-md shadow-lg`;
        toast.innerHTML = `
            <span>${message}</span>
            <button class="btn btn-sm btn-ghost" onclick="this.parentElement.remove()">✕</button>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    },
    
    /**
     * Mostra/nasconde loading overlay
     */
    showLoading(show = true) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    },
    
    /**
     * Formatta numeri con separatori migliaia
     */
    formatNumber(num) {
        return num.toLocaleString();
    },
    
    /**
     * Formatta valuta USD
     */
    formatCurrency(amount) {
        return `$${amount.toLocaleString()}`;
    },
    
    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};
