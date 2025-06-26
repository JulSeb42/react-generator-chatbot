import { useState, useRef, type KeyboardEvent } from "react"
import { BiImage, BiSend, BiTrash, BiX } from "react-icons/bi"
import axios from "axios"
import { toast } from "react-toastify"
import { chatService } from "api"
import { ButtonIcon } from "components/ButtonIcon"
import { DeleteChat } from "./DeleteChat"
import type { Chat } from "types"

export const Input: FC<IInput> = ({
	chats,
	setChats,
	isLoading,
	setIsLoading,
}) => {
	const session_id = localStorage.getItem("session_id")

	const formRef = useRef<HTMLFormElement>(null)
	const fileInputRef = useRef<HTMLInputElement>(null)
	const [isDeleteOpen, setIsDeleteOpen] = useState(false)

	const [message, setMessage] = useState("")
	const [selectedImage, setSelectedImage] = useState<File | null>(null)
	const [imagePreview, setImagePreview] = useState<string | null>(null)
	const [cloudinaryUrl, setCloudinaryUrl] = useState<string | null>(null)
	const [isUploading, setIsUploading] = useState(false)

	const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault()
			if (message.length || selectedImage) handleSubmit(e as any) // Submit the form
		}
	}

	const uploadToCloudinary = async (file: File): Promise<string | null> => {
		try {
			setIsUploading(true)

			const formData = new FormData()
			formData.append("image", file, file.name)

			console.log("=== UPLOADING TO CLOUDINARY ===")

			const response = await axios.post(
				"http://localhost:8000/api/chat/upload-image",
				formData,
				{
					headers: {
						"Content-Type": "multipart/form-data",
					},
				},
			)

			console.log("✅ Cloudinary upload success:", response.data)
			return response.data.image_url
		} catch (error) {
			console.error("❌ Cloudinary upload failed:", error)
			toast.error("Failed to upload image")
			return null
		} finally {
			setIsUploading(false)
		}
	}

	const handleImageSelect = async (
		e: React.ChangeEvent<HTMLInputElement>,
	) => {
		const file = e.target.files?.[0]

		if (!file) return

		console.log("=== FILE SELECTION ===")
		console.log("Selected file:", {
			name: file.name,
			size: file.size,
			type: file.type,
		})

		// Validate file type
		if (!file.type.startsWith("image/")) {
			toast.error("Please select an image file")
			return
		}

		// Validate file size (max 5MB)
		if (file.size > 5 * 1024 * 1024) {
			toast.error("Image size should be less than 5MB")
			return
		}

		// Set the selected file and create preview
		setSelectedImage(file)

		// Create local preview
		const reader = new FileReader()
		reader.onload = e => {
			const result = e.target?.result as string
			setImagePreview(result)
		}
		reader.readAsDataURL(file)

		// Upload to Cloudinary immediately
		const cloudinaryUrl = await uploadToCloudinary(file)
		if (cloudinaryUrl) {
			setCloudinaryUrl(cloudinaryUrl)
			toast.success("Image uploaded successfully!")
		}
	}

	const removeImage = () => {
		setSelectedImage(null)
		setImagePreview(null)
		setCloudinaryUrl(null)
		if (fileInputRef.current) {
			fileInputRef.current.value = ""
		}
	}

	const handleSubmit = async (e: FormEvent) => {
		e.preventDefault()

		if (!message.trim() && !cloudinaryUrl) return

		setIsLoading(true)

		const currentMessage = message
		const currentCloudinaryUrl = cloudinaryUrl
		const currentSessionId = session_id

		// Create a unique temporary ID for the user message
		const tempUserId = `temp-user-${Date.now()}-${Math.random()}`

		// Clear inputs immediately
		setMessage("")
		removeImage()

		// Add user message to UI immediately with temp ID
		const userMessage = {
			_id: tempUserId,
			message: currentMessage || "Generate React code for this UI mockup",
			session_id: currentSessionId ?? null,
			role: "user" as const,
			created_at: new Date().toString(),
			image_url: currentCloudinaryUrl ?? undefined,
		}

		console.log("=== ADDING USER MESSAGE ===", userMessage)
		setChats(prevChats => [...prevChats, userMessage])

		try {
			console.log("=== SENDING MESSAGE WITH CLOUDINARY URL ===")

			const response = await chatService.newChat({
				message:
					currentMessage || "Generate React code for this UI mockup",
				session_id: currentSessionId ?? "",
				image_url: currentCloudinaryUrl,
			})

			console.log("✅ Chat response:", response.data)

			// Update session if new one was created
			if (!currentSessionId && response?.data?.session_id) {
				localStorage.setItem("session_id", response.data.session_id)
			}

			// IMPORTANT: Add assistant response as a NEW message, don't modify existing ones
			if (response?.data) {
				const assistantMessage = {
					...response.data,
					_id: response.data._id || `assistant-${Date.now()}`,
					role: "assistant" as const,
				}

				console.log(
					"=== ADDING ASSISTANT MESSAGE ===",
					assistantMessage,
				)
				setChats(prevChats => [...prevChats, assistantMessage])
			}
		} catch (err: any) {
			console.error("=== CHAT ERROR ===", err)
			toast.error(`Error: ${err.response?.data?.error || err.message}`)

			// Remove the user message on error using the temp ID
			setChats(prevChats =>
				prevChats.filter(chat => chat._id !== tempUserId),
			)
		} finally {
			setIsLoading(false)
		}
	}

	return (
		<>
			<DeleteChat
				isOpen={isDeleteOpen}
				setIsOpen={setIsDeleteOpen}
				setChats={setChats}
			/>

			{imagePreview && (
				<div className="relative mb-4">
					<img
						src={imagePreview}
						alt="Selected"
						className="border border-gray-300 rounded-lg max-h-32"
					/>
					<button
						type="button"
						onClick={removeImage}
						className="-top-2 -right-2 absolute bg-red-500 hover:bg-red-600 p-1 rounded-full text-white"
					>
						<BiX size={16} />
					</button>
					{isUploading && (
						<div className="absolute inset-0 flex justify-center items-center bg-black bg-opacity-50 rounded-lg">
							<span className="text-white text-sm">
								Uploading...
							</span>
						</div>
					)}
					{cloudinaryUrl && !isUploading && (
						<div className="right-0 bottom-0 left-0 absolute bg-green-500 p-1 rounded-b-lg text-white text-xs">
							✅ Uploaded
						</div>
					)}
				</div>
			)}

			<form
				onSubmit={handleSubmit}
				className="flex items-end gap-2 w-full"
				ref={formRef}
			>
				<textarea
					className="flex backdrop-bg px-4 border-1 border-white border-solid rounded-lg outline-0 w-full min-h-[32px] field-sizing-content resize-none disabled:cursor-not-allowed"
					value={message}
					onChange={e => setMessage(e.target.value)}
					onKeyDown={handleKeyDown}
					rows={1}
					placeholder="Type your message here..."
					autoFocus
				/>

				{/* Hidden file input */}
				<input
					type="file"
					ref={fileInputRef}
					onChange={handleImageSelect}
					accept="image/*"
					style={{ display: "none" }}
				/>

				{/* Image upload button */}
				<ButtonIcon
					icon={<BiImage />}
					onClick={() => fileInputRef.current?.click()}
					tooltip="Upload image"
					disabled={isLoading || isUploading}
					type="button"
				/>

				<ButtonIcon
					icon={<BiSend />}
					type="submit"
					disabled={isLoading || (!message.length && !selectedImage)}
					tooltip="Send"
				/>

				<ButtonIcon
					icon={<BiTrash />}
					onClick={() => setIsDeleteOpen(true)}
					tooltip="Delete chat"
					disabled={!chats.length}
					role="button"
					aria-label="Delete chat"
					type="button"
				/>
			</form>
		</>
	)
}

interface IInput {
	chats: Array<Chat>
	setChats: DispatchState<Array<Chat>>
	isLoading: boolean
	setIsLoading: DispatchState<boolean>
}
