# Compare Sitemaps

## About this Project

This code is supposed to be used as a serverless function deployed to GCP. The function is to compare sitemaps and post a summary on GitHub PR. 

This function helps compare sitemaps between the production and the preview environments in QA. You no longer have to visit sitemap pages and compare them with your eyes.


## Table of Contents
1. [Tech Stack](#tech-stack)
2. [How to Use](#how-to-use)
3. [Setup](#setup)
    1. [Code](#code)
    2. [Vercel](#vercel)
4. [Deployment](#deployment)
    1. [GCP](#gcp)
    2. [Deploy the Function](#deploy-the-function)


## Tech Stack

<div align="center">
	<table>
		<tr>
			<td><code><img width="50" src="https://user-images.githubusercontent.com/25181517/192108374-8da61ba1-99ec-41d7-80b8-fb2f7c0a4948.png" alt="GitHub" title="GitHub"/></code></td>
			<td><code><img width="50" src="https://user-images.githubusercontent.com/25181517/183423507-c056a6f9-1ba8-4312-a350-19bcbc5a8697.png" alt="Python" title="Python"/></code></td>
			<td><code><img width="50" src="https://user-images.githubusercontent.com/25181517/183423775-2276e25d-d43d-4e58-890b-edbc88e915f7.png" alt="Flask" title="Flask"/></code></td>
			<td><code><img width="50" src="https://user-images.githubusercontent.com/25181517/183911547-990692bc-8411-4878-99a0-43506cdb69cf.png" alt="GCP" title="GCP"/></code></td>
		</tr>
	</table>
</div>

- **Python**: Core programming language for implementing the function.
- **Flask**: Lightweight web framework for handling HTTP requests.
- **Google Cloud Functions**: Serverless execution environment for deploying the function.
- **GitHub API**: For posting comments on pull requests.


## How to Use
Add a comment with specific keywords and URL in Github PR

(In the example image below, the keywords are "tommy," "compare," and "sitemap.")

![PR Comment](./assets/pr_comment.png)

Then, a comment will be returned, like the image below:

![PR Return Comment](./assets/pr_return_comment.png)

### Demo

On [this page](https://github.com/), please post the comment below:

```py
Hi Tommy, please compare sitemaps!

https://northernlightscanada-a56k80i27-ftc-web-dev.vercel.app
```

You are not able to compare sitemaps of your preview website with production one because `URL_PAIRS` should be set up in the code.

## Setup

### Code

1. Update `config.py` file
- `ALLOWED_ORIGINS`:
    ```py
    ALLOWED_ORIGINS = [
        'https://api.github.com',
    ]
    ```
    
    No need to update as long as you want to use this function for Github webhooks

- `KEYWORDS`:
    ```py
    KEYWORDS = ['tommy', 'compare', 'sitemap']
    ```

    List all keywords that should be included in a comment to execute this function

- `URL_PAIRS`:
    ```py
    URL_PAIRS = {
        'https://canadiantrainvacations.com': 'canadiantrainvacations',
        'https://canadapolarbears.com': 'canadapolarbears',
        'https://northernlightscanada.com': 'northernlightscanada',
        'https://freshtrackscanada.com': 'freshtrackscanada'
    }
    ```

    Key should be a production (base) URL while a value should be a keyword included in a preview URL



2. Issue Github Token (classic)

    Select the following scopes:

    - **repo** (Full control of private repositories)
    - **write:discussion** (Read and write team discussions)

### Vercel
- Turn off "Vercel Authentication" in Deployment Protection to allow the endpoint to access preview pages
![Vercel Authentication](./assets/vercel_screenshot.png)


## Deployment

### GCP

#### Prerequisit

- Created a GCP Project
- Enabled the Cloud Functions API:
    - In the GCP Console, navigate to APIs & Services > Library.
    - Enable the Cloud Functions API.
- Installed the Google Cloud SDK
    - Downloaded and installed the Google Cloud SDK
    - Initialized the SDK:

    ```
    gcloud init
    ```
    (Follow the prompts to select your project and set up your environment.)


### Deploy the Function

Please add `--set-env-vars GITHUB_TOKEN=your-github-token` at the end of the following command.


```
gcloud functions deploy compareSitemaps \
  --runtime python38 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point compare_sitemaps \
```
