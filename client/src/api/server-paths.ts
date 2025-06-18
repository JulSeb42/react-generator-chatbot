export const BASE_API_URL = `${import.meta.env.VITE_API_URL}/api`

const SERVER_PATHS_ROOT = {
	CHAT: "/chat",
}

export const SERVER_PATHS = {
	CHAT: {
		ROOT: SERVER_PATHS_ROOT.CHAT,
		ALL_CHATS: "/chats",
	},
}
