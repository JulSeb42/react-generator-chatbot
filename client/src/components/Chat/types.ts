import type { Chat } from "types"

export interface IChat {
	messages: Array<Chat>
	setMessages: DispatchState<Array<Chat>>
}
