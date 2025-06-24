export const BASE_API_URL = `${import.meta.env.VITE_API_URL}/api`

const SERVER_PATHS_ROOT = {
	CHAT: "/chat",
}

export const SERVER_PATHS = {
	CHAT: {
		ROOT: SERVER_PATHS_ROOT.CHAT,
		NEW_CHAT: `${SERVER_PATHS_ROOT.CHAT}/new-chat`,
		NEW_MESSAGE: (sessionId = ":sessionId") =>
			`${SERVER_PATHS_ROOT.CHAT}/new-message/${sessionId}`,
		SESSION_MESSAGES: (sessionId = ":sessionId") =>
			`${SERVER_PATHS_ROOT.CHAT}/messages/${sessionId}`,
		DELETE_SESSION: (sessionId = ":sessionId") =>
			`${SERVER_PATHS_ROOT.CHAT}/delete-session/${sessionId}`,
	},
}
