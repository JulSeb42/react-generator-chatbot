import { http } from "./http-common"
import { SERVER_PATHS } from "./server-paths"
import type { Chat, ApiResponse } from "types"

const { CHAT: PATHS } = SERVER_PATHS

class ChatService {
	allChats(): ApiResponse<Array<Chat>> {
		return http.get("/chat/chats")
	}

	newChat(data: {
		message: string
		session_id?: string | null
	}): ApiResponse<Chat> {
		return http.post(PATHS.NEW_CHAT, data)
	}

	newMessage(sessionId: string, message: string): ApiResponse<Array<Chat>> {
		return http.put(PATHS.NEW_MESSAGE(sessionId), message)
	}

	sessionMessages(sessionId: string) {
		return http.get(PATHS.SESSION_MESSAGES(sessionId))
	}

	deleteSession(sessionId: string) {
		return http.delete(PATHS.DELETE_SESSION(sessionId))
	}
}

export const chatService = new ChatService()
