# Welcome to your Lovable project

## Project info

**URL**: https://lovable.dev/projects/3f2cec2d-e865-4e36-af41-49d6a4da1e7c

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/3f2cec2d-e865-4e36-af41-49d6a4da1e7c) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/3f2cec2d-e865-4e36-af41-49d6a4da1e7c) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)

## Local Development

Follow these steps to run the full application locally (backend and frontend):

1. **Python backend**
   1. Create and activate a virtual environment in the project root:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
   2. Upgrade packaging tools:
      ```bash
      pip install --upgrade pip setuptools wheel
      ```
   3. Install Python dependencies, including the editable `obsidian-agent` package:
      ```bash
      pip install -r requirements.txt
      ```
   4. Create a `.env` file in the root (or copy `.env.example`) and set your OpenAI API key:
      ```text
      OPENAI_API_KEY=sk-...
      VAULT_PATH=/path/to/your/obsidian/vault
      PYTHONPATH=${workspaceFolder}/obsidian-agent
      FLASK_PORT=5000  # optional: override default port
      ```
   5. Start the Flask server:
      ```bash
      python app.py
      ```

2. **React frontend**
   1. Install Node.js dependencies:
      ```bash
      npm install
      ```
   2. Verify the API proxy in `vite.config.ts` matches the `FLASK_PORT` if you overrode it.
   3. Run the Vite development server:
      ```bash
      npm run dev
      ```
   4. Open your browser to `http://localhost:8080` to access the app.

3. **Troubleshooting**
   - If you see Pylance import errors for `agent.*`, ensure the `.env` file and VS Code setting `python.envFile` point to the root `.env`, or add `obsidian-agent/` to `python.analysis.extraPaths` in `.vscode/settings.json`.
   - If port 5000 is in use, set `FLASK_PORT` to another value and update the Vite proxy accordingly.
