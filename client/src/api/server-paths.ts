export const BASE_API_URL = `${import.meta.env.VITE_API_URL}/api`

const SERVER_PATHS_ROOT = {
	CHAT: "/chat",
}

export const SERVER_PATHS = {
	CHAT: {
		ROOT: SERVER_PATHS_ROOT.CHAT,
		NEW_CHAT: `${SERVER_PATHS_ROOT.CHAT}/new-chat`,
		NEW_MESSAGE: (session_id = ":session_id") =>
			`${SERVER_PATHS_ROOT.CHAT}/new-message/${session_id}`,
		SESSION_MESSAGES: (session_id = ":session_id") =>
			`${SERVER_PATHS_ROOT.CHAT}/messages/${session_id}`,
		DELETE_SESSION: (session_id = ":session_id") =>
			`${SERVER_PATHS_ROOT.CHAT}/delete-session/${session_id}`,
	},
}
