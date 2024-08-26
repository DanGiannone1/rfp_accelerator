#Write me a python file that will read my code files I specify and write to a local text file all the code with the filename identified

import os
# Specify the directory containing the code files
directory = 'D:/projects/rfp_accelerator/rfp_accelerator/'
files = [
     'backend/app.py',
     #'backend/search.py',
     'backend/helper_functions.py',
     #'backend/upload.py',
     #'backend/extraction.py',
     #'backend/global_vars.py',
     #'front-end/src/App.js',
     #'front-end/src/pages/MainPage.js',
     #'front-end/src/pages/RFPUploadPage.js',
     #'front-end/src/pages/EmployeeMatchingPage.js',
     'front-end/src/components/rfp/RFPListContext.js',
     #'front-end/src/components/rfp/RFPListItem.js',
     #'front-end/src/components/layout/Layout.js',
     #'front-end/src/components/layout/Sidebar.js',
     'front-end/src/pages/RFPAnalyzerPage.js',
     #'front-end/src/pages/RequirementsExtractionPage.js',
     #'front-end/src/pages/AgentMode.js',
     #'front-end/src/pages/CopilotMode.js',
     'front-end/src/components/rfp/RFPSelector.js',
     #'front-end/src/components/rfp/ExperienceSkillsetProfile.js',
     #'front-end/src/components/rfp/ArtifactDownload.js',
]

# Specify the output file path
output_file = 'D:/temp/tmp_codebase/codebase.txt'

# Open the output file in write mode
with open(output_file, 'w') as f:
    # Iterate over all files in the directory
    for filename in files:
        # Open the file in read mode
        with open(os.path.join(directory, filename), 'r') as code_file:
            # Write the filename to the output file
            f.write(f"<File: {filename}>\n")
            # Write the code from the file to the output file
            f.write(code_file.read())
            # Add a separator between files
            f.write('\n' + '-'*80 + '\n')