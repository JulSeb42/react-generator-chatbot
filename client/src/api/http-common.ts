/*
    Create API link
*/

import axios from "axios"
import { BASE_API_URL } from "./server-paths"

export const http = axios.create({
	baseURL: BASE_API_URL,
	headers: {
		"Content-type": "application/json",
		// "Access-Control-Allow-Headers": "*",
		// "Access-Control-Allow-Origin": "http://localhost:5173",
	},
	// withCredentials: true,
})
