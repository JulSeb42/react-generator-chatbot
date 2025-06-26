import { http } from "./http-common"
import { SERVER_PATHS } from "./server-paths"
import type { Chat, ApiResponse } from "types"

const { CHAT: PATHS } = SERVER_PATHS

class ChatService {
	allChats(): ApiResponse<Array<Chat>> {
		return http.get("/chat/chats")
	}

	async newChat(data: {
		message?: string
		session_id?: string | null
		image_url?: string | null
	}): Promise<ApiResponse<Chat>> {
		try {
			const response = await http.post(PATHS.NEW_CHAT, data, {
				headers: { "Content-Type": "application/json" },
			})

			return response
		} catch (error) {
			console.error("❌ Chat service error:", error)
			throw error
		}
	}

	newMessage(session_id: string, message: string): ApiResponse<Array<Chat>> {
		return http.put(PATHS.NEW_MESSAGE(session_id), message)
	}

	sessionMessages(session_id: string) {
		return http.get(PATHS.SESSION_MESSAGES(session_id))
	}

	deleteSession(session_id: string) {
		return http.delete(PATHS.DELETE_SESSION(session_id))
	}
}

export const chatService = new ChatService()
