/**
 * Componente Testing
 */
const TestingComponent = {
    async executeFlow() {
        try {
            const input = document.getElementById('test-input').value.trim();
            const output = document.getElementById('test-output');
            output.innerHTML = '<div class="loading loading-spinner loading-lg"></div>';
            
            const result = await API.post('/core/v1/ai/query', {
                message: input,
                app_id: State.appId || 'default'
            });
            
            output.innerHTML = `
                <div class="card bg-base-100 shadow-xl">
                    <div class="card-body">
                        <h2 class="card-title">Response</h2>
                        <p>${result.response || result.message || 'No response'}</p>
                        ${result.credits_used ? `<p class="text-sm text-gray-500">Credits used: ${result.credits_used}</p>` : ''}
                    </div>
                </div>
            `;
        } catch (error) {
            document.getElementById('test-output').innerHTML = `
                <div class="alert alert-error">
                    <i class="fas fa-exclamation-circle"></i>
                    <span>Error: ${error.message}</span>
                </div>
            `;
        }
    }
};