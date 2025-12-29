// main.js

const { app, dialog } = require("electron");
const path = require("path");
const fs = require("fs");

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
    if (argument.startsWith("--") === true) {
      const parts = argument.slice(2).split("=");
      const key = parts[0];
      let value = parts.length > 1 ? parts.slice(1).join("=") : true;

      // Type conversion for boolean values
      if (value === "true") value = true;
      if (value === "false") value = false;

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

  const TITLE = arguments.title || "Multi Directory Picker";
  let INITIAL_PATH = undefined;

  if (arguments.default_path) {
    const candidatePath = path.resolve(arguments.default_path);

    try {
      const statistics = fs.lstatSync(candidatePath);

      if (statistics.isDirectory() === true) {
        INITIAL_PATH = candidatePath;
      } else {
        console.warn(
          `defaultPath exists but is not a directory: ${candidatePath}`
        );
      }
    } catch (error) {
      console.warn(`defaultPath is inaccessible or invalid: ${candidatePath}`);
    }
  }

  const RETURN_FULL_PATHS = arguments.return_full_paths === true;
  const properties = ["openDirectory", "multiSelections"];

  const dialogOptions = {
    title: TITLE,
    ...(INITIAL_PATH && { defaultPath: INITIAL_PATH }),
    properties: properties,
    message: "Select folder(s). Use Ctrl/Cmd or Shift for multi-selection.",
  };

  let selectedPaths = dialog.showOpenDialogSync(dialogOptions);
  if (!selectedPaths) selectedPaths = [];

  if (selectedPaths.length > 0) {
    if (!RETURN_FULL_PATHS) {
      finalPaths = selectedPaths.map(current_path =>
        path.basename(current_path)
      );
    }
  }

  process.stdout.write(JSON.stringify(finalPaths) + "\n");
  app.exit(0);
}

app.whenReady().then(pickFoldersAndOutput);
