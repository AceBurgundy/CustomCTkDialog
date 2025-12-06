// main.js

const { app, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

// Set AppUserModelId for command-line behavior (Critical on Windows)
app.setAppUserModelId(process.execPath);

/**
 * Parses command-line arguments passed to the Node process.
 * Expected format: --key=value
 * @returns {Object} An object mapping argument names to their values.
 */
function parseArguments() {
    const arguments = {};
    const rawArguments = process.argv.slice(0); 

    for (const argument of rawArguments) { 
        if (argument.startsWith('--') === true) {
            const parts = argument.slice(2).split('=');
            const key = parts[0];
            let value = parts.length > 1 ? parts.slice(1).join('=') : true;
            
            // Type conversion for boolean values
            if (value === 'true') value = true;
            if (value === 'false') value = false;
            
            arguments[key] = value;
        }
    }
    
    return arguments;
}

/**
 * Executes the folder picker logic based on command-line arguments.
 */
function pickFoldersAndOutput() {
    const arguments = parseArguments();

    const DEFAULT_TITLE = arguments.title || 'Multi Directory Picker';
    let DEFAULT_PATH = undefined; 

    if (arguments.default_path) {
        const candidatePath = path.resolve(arguments.default_path);

        try {
            const stats = fs.lstatSync(candidatePath);

            if (stats.isDirectory() === true) {
                DEFAULT_PATH = candidatePath; 
            } else {
                console.warn(`defaultPath exists but is not a directory: ${candidatePath}`);
            }

        } catch (error) {
            console.warn(`defaultPath is inaccessible or invalid: ${candidatePath}`);
        }
    }

    const RETURN_FULL_PATHS = arguments.return_full_paths === true;
    const properties = ['openDirectory', 'multiSelections'];
    
    const dialogOptions = {
        title: DEFAULT_TITLE,
        ...(DEFAULT_PATH && { defaultPath: DEFAULT_PATH }), 
        properties: properties,
        message: 'Select folder(s). Use Ctrl/Cmd or Shift for multi-selection.'
    };

    const selectedPaths = dialog.showOpenDialogSync(dialogOptions);
    
    let finalPaths = [];

    if (selectedPaths && selectedPaths.length > 0) {
        if (RETURN_FULL_PATHS) {
            finalPaths = selectedPaths;
        } else {
            finalPaths = selectedPaths.map(current_path => path.basename(current_path));
        }
    }

    // Output the resulting array (empty if cancelled) as JSON to stdout    
    process.stdout.setDefaultEncoding('utf8');
    process.stdout.write(Buffer.from(JSON.stringify(finalPaths), 'utf8'));
}

app.whenReady().then(pickFoldersAndOutput);

app.on('window-all-closed', () => {
    app.quit(); 
});