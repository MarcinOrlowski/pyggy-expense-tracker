/**
 * Enhanced Amount Input Sanitization
 * 
 * Provides real-time sanitization for amount input fields to support
 * international number formats and copy-paste operations.
 * 
 * Features:
 * - Supports both comma (,) and dot (.) as decimal separators
 * - Removes currency symbols (€, $, £, zł, etc.)
 * - Handles thousand separators and spaces
 * - Real-time feedback during typing and paste operations
 */

class AmountSanitizer {
    constructor() {
        this.currencyPattern = /[$€]|zł|zl/gi;
    }

    /**
     * Sanitize input string to extract numeric value
     * @param {string} value - Raw input string
     * @returns {string} - Sanitized numeric string using dot notation
     */
    sanitize(value) {
        if (!value || typeof value !== 'string') {
            return value;
        }

        // Remove leading/trailing whitespace
        value = value.trim();

        // Remove currency symbols
        value = value.replace(this.currencyPattern, '');

        // Remove extra spaces
        value = value.replace(/\s+/g, ' ').trim();

        // Handle thousand separators and decimal separators
        // Look for the last occurrence of comma or dot with 1-2 digits after it
        const decimalMatch = value.match(/[,.](\d{1,2})(?:\s|[^\d]|$)/);
        
        let sanitized;
        
        if (decimalMatch) {
            // Found a potential decimal separator
            const decimalPos = decimalMatch.index;
            const decimalSeparator = value[decimalPos];
            
            // Everything before the decimal separator
            let integerPart = value.substring(0, decimalPos);
            // The decimal part (digits after separator)
            const decimalPart = decimalMatch[1];
            
            // Clean the integer part: remove all separators and spaces
            integerPart = integerPart.replace(/[,.\s]/g, '');
            
            // Combine with dot as decimal separator
            sanitized = decimalPart ? `${integerPart}.${decimalPart}` : integerPart;
        } else {
            // No decimal separator found, treat as integer
            // Remove all non-digit characters except minus sign at the beginning
            sanitized = value.replace(/[^\d-]/g, '');
        }

        // Handle negative numbers (preserve minus sign at the beginning)
        if (value.trim().startsWith('-') && !sanitized.startsWith('-')) {
            sanitized = '-' + sanitized;
        }

        // Remove any remaining non-numeric characters except dot and minus
        sanitized = sanitized.replace(/[^\d.-]/g, '');

        // Ensure only one decimal point
        const parts = sanitized.split('.');
        if (parts.length > 2) {
            // Multiple decimal points, keep only the last one
            const integerPart = parts.slice(0, -1).join('');
            const decimalPart = parts[parts.length - 1];
            sanitized = `${integerPart}.${decimalPart}`;
        }

        // Basic validation - return original if sanitization produces invalid result
        if (sanitized && !['', '-', '.', '-.'].includes(sanitized)) {
            // Test if it's a valid number
            if (!isNaN(parseFloat(sanitized))) {
                return sanitized;
            }
        }

        // If sanitization fails, return empty string to avoid confusion
        return '';
    }

    /**
     * Apply sanitization to an input field
     * @param {HTMLInputElement} input - The input element to sanitize
     * @param {boolean} updateValue - Whether to update the input value
     * @returns {string} - The sanitized value
     */
    sanitizeInput(input, updateValue = false) {
        const originalValue = input.value;
        const sanitizedValue = this.sanitize(originalValue);
        
        if (updateValue && sanitizedValue !== originalValue) {
            // Store cursor position
            const cursorPos = input.selectionStart;
            
            // Update value
            input.value = sanitizedValue;
            
            // Restore cursor position (adjust for length difference)
            const lengthDiff = sanitizedValue.length - originalValue.length;
            const newCursorPos = Math.max(0, cursorPos + lengthDiff);
            input.setSelectionRange(newCursorPos, newCursorPos);
            
            // Trigger input event to notify other listeners
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        return sanitizedValue;
    }

    /**
     * Initialize sanitization for amount input fields
     */
    init() {
        // Find all amount input fields
        const amountInputs = document.querySelectorAll('input[name="total_amount"], input[name="initial_amount"], input[name="amount"]');
        
        amountInputs.forEach(input => {
            this.attachListeners(input);
        });
    }

    /**
     * Attach event listeners to an input field
     * @param {HTMLInputElement} input - The input element
     */
    attachListeners(input) {
        // Handle paste events
        input.addEventListener('paste', (event) => {
            // Allow the paste to happen first, then sanitize
            setTimeout(() => {
                this.sanitizeInput(input, true);
            }, 0);
        });

        // Handle input events (typing)
        input.addEventListener('input', (event) => {
            // Only sanitize if the input looks like it might need it
            // (contains currency symbols, multiple separators, etc.)
            const value = input.value;
            if (this.needsSanitization(value)) {
                this.sanitizeInput(input, true);
            }
        });

        // Handle blur events (when user leaves the field)
        input.addEventListener('blur', (event) => {
            this.sanitizeInput(input, true);
        });

        // Add visual feedback for supported formats
        this.addVisualFeedback(input);
    }

    /**
     * Check if a value needs sanitization
     * @param {string} value - The input value
     * @returns {boolean} - Whether sanitization is needed
     */
    needsSanitization(value) {
        if (!value) return false;
        
        // Check for currency symbols
        if (this.currencyPattern.test(value)) return true;
        
        // Check for spaces in numbers
        if (/\d\s+\d/.test(value)) return true;
        
        // Check for comma as decimal separator
        if (/\d,\d/.test(value)) return true;
        
        // Check for thousand separators
        if (/\d[,.\s]\d{3}/.test(value)) return true;
        
        return false;
    }

    /**
     * Add visual feedback to indicate supported formats
     * @param {HTMLInputElement} input - The input element
     */
    addVisualFeedback(input) {
        // Add a title attribute with examples
        if (!input.title) {
            input.title = 'Supported formats: 10.50, 10,50, $10.50, €10,50, 1 234,56';
        }
        
        // Add a CSS class for styling
        input.classList.add('amount-input-enhanced');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const sanitizer = new AmountSanitizer();
    sanitizer.init();
});

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AmountSanitizer;
}