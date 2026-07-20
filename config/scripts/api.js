/**
 * Chatify API Client
 *
 * Automatically uses the current page origin as the API URL.
 *
 * @example
 * const chat = new Chatify();
 *
 * const login = await chat.login("bob", "password");
 * const channels = await chat.getChannels();
 */

class Chatify {
    /**
     * Create a Chatify client.
     */
    constructor() {
        /**
         * API base URL.
         *
         * @type {string}
         */
        this.baseURL = location.origin;

        /**
         * Current authentication token.
         *
         * @type {string|null}
         */
        this.token = null;
    }


    /**
     * Perform an API request.
     *
     * @private
     *
     * @param {string} endpoint
     * @param {{
     *   method?: string,
     *   body?: Object
     * }} options
     *
     * @returns {Promise<any>}
     */
    async request(endpoint, options = {}) {
        const headers = {
            "Content-Type": "application/json"
        };

        if (this.token) {
            headers.Authorization = `Bearer ${this.token}`;
        }

        const response = await fetch(this.baseURL + endpoint, {
            method: options.method ?? "GET",
            headers,
            body: options.body
                ? JSON.stringify(options.body)
                : undefined
        });

        if (!response.ok) {
            throw new Error(
                `Chatify API error ${response.status}: ${await response.text()}`
            );
        }

        return response.json();
    }


    /**
     * Login to Chatify.
     *
     * @param {string} username
     * @param {string} password
     *
     * @returns {Promise<{
     * success:boolean,
     * session_token:string,
     * id:number,
     * error:string
     * }>}
     */
    async login(username, password) {
        const result = await this.request("/api/login", {
            method: "POST",
            body: {
                username,
                password
            }
        });

        if (result.success) {
            this.token = result.session_token;
        }

        return result;
    }


    /**
     * Get user information.
     *
     * @param {number} userID
     *
     * @returns {Promise<{username:string}>}
     */
    getUser(userID) {
        return this.request(`/users/${userID}`);
    }


    /**
     * Get available channels.
     *
     * @param {number} [limit=50]
     *
     * @returns {Promise<{channels:number[]}>}
     */
    getChannels(limit = 50) {
        return this.request(`/channels/get?limit=${limit}`);
    }


    /**
     * Create a channel.
     *
     * @param {string} name
     * @param {string} description
     *
     * @returns {Promise<{
     * success:boolean,
     * error:string,
     * id:number
     * }>}
     */
    createChannel(name, description) {
        return this.request("/channels/new", {
            method: "POST",
            body: {
                name,
                description
            }
        });
    }


    /**
     * Read messages from a channel.
     *
     * @param {number} channelID
     * @param {number} [limit=50]
     *
     * @returns {Promise<{messages:Object[]}>}
     */
    readChannel(channelID, limit = 50) {
        return this.request(
            `/channels/${channelID}/read?limit=${limit}`
        );
    }


    /**
     * Send a message.
     *
     * @param {number} channelID
     * @param {string} content
     * @param {number} author
     *
     * @returns {Promise<Object>}
     */
    sendMessage(channelID, content, author) {
        return this.request(`/channels/${channelID}/send`, {
            method: "POST",
            body: {
                content,
                author
            }
        });
    }


    /**
     * Manually set authentication token.
     *
     * @param {string} token
     */
    setToken(token) {
        this.token = token;
    }


    /**
     * Log out and remove token.
     */
    logout() {
        this.token = null;
    }
}


export default Chatify;