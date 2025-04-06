import Composio from 'composio-core';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Verifies the Composio LinkedIn integration configuration
 *
 * This function fetches integration details from Composio and verifies that:
 * 1. The integration exists and is accessible
 * 2. The integration is properly configured for LinkedIn
 * 3. The integration has the necessary permissions
 * 4. The integration matches the expected configuration in the .env file
 *
 * @returns {Promise<Object|null>} The integration details if successful, null otherwise
 */
async function getIntegrationDetails() {
  try {
    // Get API key from environment variables or use default
    const apiKey = process.env.COMPOSIO_API_KEY || "3kc5iwkpu3rtdk6cbvfuop";
    
    // Get integration ID from environment variables or use default
    const integrationId = process.env.COMPOSIO_INTEGRATION_ID || "53db8a77-df94-4544-b352-3c08a1110a37";
    
    console.log(`Verifying Composio LinkedIn integration (ID: ${integrationId})...`);
    
    // Initialize Composio client
    const composio = new Composio({ apiKey });
    
    // Get integration details
    const integration = await composio.integrations.get({
      integrationId
    });
    
    if (!integration) {
      console.error(`Integration with ID ${integrationId} not found`);
      return null;
    }
    
    // Log detailed integration information
    console.log("\n=== Composio LinkedIn Integration Details ===");
    console.log(`Integration ID: ${integration.id}`);
    console.log(`Name: ${integration.name}`);
    console.log(`Entity: ${integration.entity}`);
    console.log(`Status: ${integration.status || 'Unknown'}`);
    console.log(`Created: ${integration.createdAt ? new Date(integration.createdAt).toLocaleString() : 'Unknown'}`);
    console.log(`Last Updated: ${integration.updatedAt ? new Date(integration.updatedAt).toLocaleString() : 'Unknown'}`);
    
    // Verify LinkedIn-specific configuration
    if (integration.entity !== 'linkedin') {
      console.error(`ERROR: Integration entity is "${integration.entity}" but expected "linkedin"`);
      return null;
    }
    
    // Check if the integration has the necessary scopes/permissions
    const requiredScopes = ['w_member_social'];
    const missingScopes = [];
    
    if (integration.scopes) {
      console.log(`Scopes: ${integration.scopes.join(', ')}`);
      
      for (const scope of requiredScopes) {
        if (!integration.scopes.includes(scope)) {
          missingScopes.push(scope);
        }
      }
    } else {
      console.log('Scopes: Not available');
      missingScopes.push(...requiredScopes);
    }
    
    if (missingScopes.length > 0) {
      console.warn(`WARNING: Integration is missing required scopes: ${missingScopes.join(', ')}`);
    }
    
    // Verify the integration matches the expected configuration in .env
    const expectedOrgUrn = process.env.ORGANIZATION_URN;
    if (expectedOrgUrn && integration.organizationUrn && expectedOrgUrn !== integration.organizationUrn) {
      console.warn(`WARNING: Organization URN mismatch. Expected: ${expectedOrgUrn}, Actual: ${integration.organizationUrn}`);
    }
    
    // Check if the integration is active
    if (integration.status && integration.status !== 'active') {
      console.error(`ERROR: Integration status is "${integration.status}" but expected "active"`);
    } else {
      console.log('✅ Integration is active and properly configured for LinkedIn');
    }
    
    // Check if the integration has the expected tool name
    const expectedToolName = process.env.COMPOSIO_LINKEDIN_TOOL || 'LINKEDIN_MCP_CREATE_LINKED_IN_POST';
    if (integration.tools) {
      const hasExpectedTool = integration.tools.some(tool =>
        tool.name === expectedToolName || tool.id === expectedToolName
      );
      
      if (hasExpectedTool) {
        console.log(`✅ Integration has the expected tool: ${expectedToolName}`);
      } else {
        console.warn(`WARNING: Integration does not have the expected tool: ${expectedToolName}`);
        console.log('Available tools:', integration.tools.map(t => t.name || t.id).join(', '));
      }
    }
    
    console.log("=== End of Integration Details ===\n");
    
    return integration;
  } catch (error) {
    console.error("Error verifying Composio LinkedIn integration:", error);
    console.error("Stack trace:", error.stack);
    return null;
  }
}

// Execute the function
getIntegrationDetails()
  .then(integration => {
    if (integration) {
      console.log("Integration verification completed successfully");
    } else {
      console.error("Integration verification failed");
      process.exit(1);
    }
  })
  .catch(error => {
    console.error("Unexpected error during integration verification:", error);
    process.exit(1);
  });