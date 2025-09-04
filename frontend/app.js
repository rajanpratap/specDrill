class APITestGenerator {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.currentTestCases = null;
    }

    initializeElements() {
        this.elements = {
            input: document.getElementById('openapi-input'),
            generateBtn: document.getElementById('generate-btn'),
            clearBtn: document.getElementById('clear-btn'),
            sampleBtn: document.getElementById('sample-btn'),
            downloadBtn: document.getElementById('download-btn'),
            copyBtn: document.getElementById('copy-btn'),
            copyBtnText: document.querySelector('#copy-btn .copy-text'),
            outputSection: document.getElementById('output-section'),
            resultOutput: document.getElementById('result-output'),
            resultInfo: document.getElementById('result-info'),
            loadingOverlay: document.getElementById('loading-overlay'),
            toastContainer: document.getElementById('toast-container')
        };
    }

    attachEventListeners() {
        this.elements.generateBtn.addEventListener('click', () => this.generateTestCases());
        this.elements.clearBtn.addEventListener('click', () => this.clearInput());
        this.elements.sampleBtn.addEventListener('click', () => this.loadSample());
        this.elements.downloadBtn.addEventListener('click', () => this.downloadResults());
        this.elements.copyBtn.addEventListener('click', () => this.copyToClipboard());
        this.elements.input.addEventListener('input', () => this.autoResizeTextarea());
    }

    autoResizeTextarea() {
        const textarea = this.elements.input;
        textarea.style.height = 'auto';
        textarea.style.height = Math.max(350, textarea.scrollHeight) + 'px';
    }

    async generateTestCases() {
        const input = this.elements.input.value.trim();
        if (!input) {
            this.showToast('Please paste your OpenAPI specification', 'warning');
            return;
        }

        let openApiSpec;
        try {
            openApiSpec = JSON.parse(input);
        } catch (error) {
            this.showToast('Invalid JSON format. Please check your specification.', 'error');
            return;
        }

        this.showLoading(true);
        this.setButtonLoading(true);

        try {
            const response = await fetch('/generate-tests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ openapi_spec: openApiSpec })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.status === 'success' && result.test_cases) {
                this.displayResults(result.test_cases, result.message);
                this.showToast('Test cases generated successfully!', 'success');
            } else {
                throw new Error(result.message || 'An unknown error occurred');
            }
        } catch (error) {
            console.error('Error generating test cases:', error);
            this.showToast(`Error: ${error.message}`, 'error');
            this.elements.outputSection.style.display = 'none';
        } finally {
            this.showLoading(false);
            this.setButtonLoading(false);
        }
    }
    
    // NEW: Function to highlight JSON syntax
    highlightJSON(jsonString) {
        if (!jsonString) return '';
        jsonString = jsonString.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return jsonString.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match) => {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'property'; // Key
                } else {
                    cls = 'string'; // String value
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return `<span class="token ${cls}">${match}</span>`;
        });
    }

    displayResults(testCases, message) {
        this.currentTestCases = testCases;
        this.elements.outputSection.style.display = 'block';
        
        this.elements.resultInfo.textContent = message || `Generated ${testCases.length} endpoint scenarios`;
        
        const formattedJson = JSON.stringify(testCases, null, 2);
        // Use the new highlighter function
        this.elements.resultOutput.innerHTML = this.highlightJSON(formattedJson);
        
        this.elements.outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    clearInput() {
        this.elements.input.value = '';
        this.elements.outputSection.style.display = 'none';
        this.currentTestCases = null;
        this.autoResizeTextarea();
        this.showToast('Input cleared', 'info');
    }

    loadSample() {
        // (Sample spec is quite long, keeping your existing sample spec logic)
        const sampleSpec = {"openapi":"3.0.0","info":{"title":"Pet Store API","version":"1.0.0","description":"A simple pet store API"},"servers":[{"url":"https://api.petstore.example.com/v1"}],"paths":{"/pets":{"get":{"summary":"List all pets","operationId":"listPets","tags":["pets"],"parameters":[{"name":"limit","in":"query","description":"How many items to return at one time (max 100)","required":false,"schema":{"type":"integer","format":"int32"}}],"responses":{"200":{"description":"A paged array of pets","content":{"application/json":{"schema":{"type":"array","items":{"$ref":"#/components/schemas/Pet"}}}}},"default":{"description":"unexpected error","content":{"application/json":{"schema":{"$ref":"#/components/schemas/Error"}}}}}},"post":{"summary":"Create a pet","operationId":"createPets","tags":["pets"],"requestBody":{"required":true,"content":{"application/json":{"schema":{"$ref":"#/components/schemas/Pet"}}}},"responses":{"201":{"description":"Null response"},"default":{"description":"unexpected error","content":{"application/json":{"schema":{"$ref":"#/components/schemas/Error"}}}}}}},"/pets/{petId}":{"get":{"summary":"Info for a specific pet","operationId":"showPetById","tags":["pets"],"parameters":[{"name":"petId","in":"path","required":true,"description":"The id of the pet to retrieve","schema":{"type":"string"}}],"responses":{"200":{"description":"Expected response to a valid request","content":{"application/json":{"schema":{"$ref":"#/components/schemas/Pet"}}}},"default":{"description":"unexpected error","content":{"application/json":{"schema":{"$ref":"#/components/schemas/Error"}}}}}}}},"components":{"schemas":{"Pet":{"type":"object","required":["id","name"],"properties":{"id":{"type":"integer","format":"int64"},"name":{"type":"string"},"tag":{"type":"string"}}},"Error":{"type":"object","required":["code","message"],"properties":{"code":{"type":"integer","format":"int32"},"message":{"type":"string"}}}}}};
        this.elements.input.value = JSON.stringify(sampleSpec, null, 2);
        this.autoResizeTextarea();
        this.showToast('Sample OpenAPI specification loaded', 'success');
    }

    downloadResults() {
        if (!this.currentTestCases) {
            this.showToast('No test cases to download', 'warning');
            return;
        }
        const blob = new Blob([JSON.stringify(this.currentTestCases, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `specdrill-test-cases-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        this.showToast('Download started!', 'success');
    }

    async copyToClipboard() {
        if (!this.currentTestCases) {
            this.showToast('No results to copy', 'warning');
            return;
        }

        const textToCopy = JSON.stringify(this.currentTestCases, null, 2);
        try {
            await navigator.clipboard.writeText(textToCopy);
            
            // NEW: Better UX feedback on copy
            const originalText = this.elements.copyBtnText.textContent;
            this.elements.copyBtnText.textContent = 'Copied!';
            this.elements.copyBtn.classList.add('success');
            
            setTimeout(() => {
                this.elements.copyBtnText.textContent = originalText;
                this.elements.copyBtn.classList.remove('success');
            }, 2000);
            
        } catch (err) {
            this.showToast('Failed to copy to clipboard', 'error');
            console.error('Clipboard copy failed:', err);
        }
    }

    showLoading(show) {
        this.elements.loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    setButtonLoading(loading) {
        const btn = this.elements.generateBtn;
        const textSpan = btn.querySelector('.btn-text');
        const spinner = btn.querySelector('.spinner');
        
        btn.disabled = loading;
        textSpan.style.display = loading ? 'none' : 'inline';
        spinner.style.display = loading ? 'inline-block' : 'none';
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        this.elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.5s ease forwards';
            toast.addEventListener('animationend', () => toast.remove());
        }, 4000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new APITestGenerator();
});