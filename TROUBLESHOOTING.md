# Troubleshooting Guide

This guide helps you resolve common issues you might encounter when using the Zep Query Client.

## Common Errors

### 1. "center_node_uuid is required when reranker is node_distance"

**Error Message:**
```
zep_cloud.errors.bad_request_error.BadRequestError: status_code: 400, body: message='bad request: center_node_uuid is required when reranker is node_distance'
```

**Solution:**
This error occurs because the `node_distance` reranker requires a centroid node to function properly. To fix this:

1. Make sure the "Use Centroid Node" checkbox is enabled when using the `node_distance` reranker
2. Enter a valid centroid query or use the "Generate with OpenAI" option
3. Ensure that the centroid query returns at least one result

The application has been updated to automatically:
- Enable the "Use Centroid Node" option when `node_distance` is selected
- Fall back to the `rrf` reranker if no centroid node is found
- Show a warning message when this happens

### 2. "Group ID not found"

**Error Message:**
```
zep_cloud.errors.not_found_error.NotFoundError: status_code: 404, body: message='not found: group not found'
```

**Solution:**
This error occurs when the Group ID you entered doesn't exist in your Zep account. To fix this:

1. Double-check that you've entered the correct Group ID
2. Verify that the Group ID exists in your Zep account
3. Make sure your Zep API key has access to this Group ID

**Setting a Default Group ID:**
To avoid having to enter your Group ID each time, you can set it in your `.env` file:

1. Run the setup script: `python setup_env.py`
2. Or manually add `ZEP_GROUP_ID=your_group_id_here` to your `.env` file

### 3. API Key Issues

**Error Message:**
```
zep_cloud.errors.unauthorized_error.UnauthorizedError: status_code: 401, body: message='unauthorized: invalid api key'
```

**Solution:**
This error occurs when your Zep API key is invalid or has expired. To fix this:

1. Check that you've created a `.env` file with your API keys
2. Verify that your Zep API key is correct and hasn't expired
3. If necessary, generate a new API key from your Zep account

### 4. OpenAI API Issues

**Error Message:**
```
openai.error.AuthenticationError: No API key provided.
```

**Solution:**
This error occurs when your OpenAI API key is missing or invalid. To fix this:

1. Check that you've added your OpenAI API key to the `.env` file
2. Verify that your OpenAI API key is correct
3. If you don't want to use OpenAI features, avoid using the "Generate with OpenAI" option

## General Troubleshooting Steps

1. **Check your API keys**: Make sure both your Zep API key and OpenAI API key are correctly set in the `.env` file
2. **Restart the application**: Sometimes simply restarting the application can resolve issues
3. **Check your internet connection**: Ensure you have a stable internet connection
4. **Update dependencies**: Make sure all dependencies are up to date by running `pip install -r requirements.txt`
5. **Check Zep status**: Verify that the Zep service is up and running

If you continue to experience issues, please open an issue on the GitHub repository with details about the problem you're encountering. 