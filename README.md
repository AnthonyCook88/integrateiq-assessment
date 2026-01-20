# Integrate IQ Assessment - HubSpot Contact Integration

This application fetches contact data from an AWS API and syncs it to HubSpot, handling duplicate email addresses by updating existing contacts instead of creating new ones.

## Prerequisites

- Python 3.7 or higher
- HubSpot Sandbox account access
- HubSpot Private Application with API key (with read/write contacts permissions)

## Setup Instructions

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `env.example` to `.env`
   ```bash
   cp env.example .env
   ```
   (On Windows PowerShell: `Copy-Item env.example .env`)
   - Open `.env` and update your HubSpot API key:
   ```
   HUBSPOT_API_KEY=your_actual_api_key_here
   ```
   - The AWS API URL and Bearer token are already in `env.example` and will be copied to `.env`

4. **Get your HubSpot API Key**
   - Log into your HubSpot Sandbox account
   - Navigate to Settings → Integrations → Private Apps
   - Create a new private app (or use an existing one)
   - Ensure it has permissions to read and write contacts
   - Copy the API key and add it to your `.env` file

## Running the Application

Simply run:
```bash
python main.py
```

The application will:
1. Fetch all contacts from the AWS API
2. For each contact, check if it already exists in HubSpot (by email)
3. Create new contacts or update existing ones as needed
4. Display progress and results

## How It Works

- **Duplicate Handling**: The application uses HubSpot's search API to check if a contact with the same email already exists. If found, it updates the existing contact instead of creating a new one, preventing duplicate email errors.

- **Data Mapping**: The application maps the following fields from the AWS API to HubSpot:
  - `email` → `email`
  - `firstname` or `firstName` → `firstname`
  - `lastname` or `lastName` → `lastname`
  - `phone` → `phone`
  - `company` → `company`

- **Idempotency**: The application can be run multiple times without creating duplicate contacts, as it always checks for existing contacts before creating new ones.

## Validation

After running the application, you can validate the contacts in HubSpot by:
1. Logging into your HubSpot Sandbox account
2. Navigating to Contacts → Contacts
3. Verifying that the contacts from the AWS API have been created or updated

## Troubleshooting

- **"HUBSPOT_API_KEY environment variable is not set"**: Make sure you've created a `.env` file with your API key
- **"Error creating/updating contact"**: Check that your HubSpot API key has the correct permissions (read/write contacts)
- **API Rate Limits**: HubSpot has rate limits. If you encounter rate limit errors, the application will display them. You may need to add retry logic or rate limiting.

## Security Notes

- Never commit your `.env` file or API keys to version control
- The `.gitignore` file is configured to exclude `.env` files
- All API keys and tokens are stored in `.env` file (not committed to git)

## Project Structure

```
.
├── main.py              # Main application code
├── requirements.txt     # Python dependencies
├── env.example          # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Contact

For questions about this assessment, contact:
- tyler@integrateiq.com
- rafael@integrateiq.com
