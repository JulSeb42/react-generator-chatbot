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
