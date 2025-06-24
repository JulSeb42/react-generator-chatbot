export type Role = "user" | "assistant"

export type Chat = {
	_id: string
	role: Role
	session_id: string | null
	message: string
	created_at: string
}
