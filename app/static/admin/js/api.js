/**
 * Client API centralizzato
 */
const API = {
    /**
     * Chiamata API generica
     */
    async call(endpoint, options = {}) {
        const url = State.getBase() + endpoint;
        const headers = State.getAuthHeaders();
        
        if (options.body && typeof options.body !== 'string') {
            options.body = JSON.stringify(options.body);
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers: { ...headers, ...options.headers }
            });
            
            const text = await response.text();
            let data;
            
            try {
                data = JSON.parse(text);
            } catch {
                if (!response.ok) throw new Error(text || response.statusText);
                return text;
            }
            
            if (!response.ok) {
                throw new Error(data.detail || data.message || response.statusText);
            }
            
            return data;
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    },
    
    /**
     * Metodi shortcuts
     */
    async get(endpoint) {
        return this.call(endpoint);
    },
    
    async post(endpoint, data) {
        return this.call(endpoint, {
            method: 'POST',
            body: data
        });
    },
    
    async put(endpoint, data) {
        return this.call(endpoint, {
            method: 'PUT',
            body: data
        });
    },
    
    async delete(endpoint) {
        return this.call(endpoint, {
            method: 'DELETE'
        });
    }
};
