import { useState, useRef, type KeyboardEvent } from "react"
import { BiImage, BiSend, BiTrash, BiX } from "react-icons/bi"
import { toast } from "react-toastify"
import { chatService } from "api"
import { clsx } from "utils"
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
	const [isDragOver, setIsDragOver] = useState(false)

	const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault()
			if (message.length || selectedImage) handleSubmit(e as any) // Submit the form
		}
	}

	const validateFile = (file: File): boolean => {
		if (!file.type.startsWith("image/")) {
			toast.error("Please select an image file")
			return false
		}

		if (file.size > 5 * 1024 * 1024) {
			toast.error("Image size should be less than 5MB")
			return false
		}

		return true
	}

	const uploadToCloudinary = async (file: File): Promise<string | null> => {
		setIsUploading(true)

		const formData = new FormData()
		formData.append("image", file, file.name)

		return chatService
			.uploadImage(formData)
			.then(res => res.data.image_url)
			.catch(err => {
				console.error("❌ Cloudinary upload failed: ", err)
				toast.error("Failed to upload image")
			})
			.finally(() => setIsUploading(false))
	}

	const processFile = async (file: File) => {
		if (!validateFile(file)) return

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
		}
	}

	const handleImageSelect = async (
		e: React.ChangeEvent<HTMLInputElement>,
	) => {
		const file = e.target.files?.[0]

		if (!file) return

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
		}
	}

	const handleDragEnter = (e: React.DragEvent) => {
		e.preventDefault()
		e.stopPropagation()
		setIsDragOver(true)
	}

	const handleDragLeave = (e: React.DragEvent) => {
		e.preventDefault()
		e.stopPropagation()
		setIsDragOver(false)
	}

	const handleDragOver = (e: React.DragEvent) => {
		e.preventDefault()
		e.stopPropagation()
	}

	const handleDrop = async (e: React.DragEvent) => {
		e.preventDefault()
		e.stopPropagation()
		setIsDragOver(false)

		const files = e.dataTransfer.files
		if (files.length > 0) {
			const file = files[0]
			await processFile(file)
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

		// Fix the condition here
		if (!message.trim() && !cloudinaryUrl) return

		setTimeout(async () => {
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
				message: message || "Generate React code for this UI mockup",
				session_id: currentSessionId ?? null,
				role: "user" as const,
				created_at: new Date().toString(),
				image_url: currentCloudinaryUrl ?? undefined,
			}

			setChats(prevChats => [...prevChats, userMessage])

			try {
				const response = await chatService.newChat({
					message:
						message || "Generate React code for this UI mockup",
					session_id: currentSessionId ?? "",
					image_url: currentCloudinaryUrl,
				})

				// Update session if new one was created
				if (!currentSessionId && response?.data?.session_id) {
					localStorage.setItem("session_id", response.data.session_id)
				}

				// Validate the response before adding it
				if (
					response?.data &&
					response.data.role === "assistant" &&
					response.data.message
				) {
					const assistantMessage = {
						_id: response.data._id || `assistant-${Date.now()}`,
						session_id: response.data.session_id,
						role: "assistant" as const,
						message: response.data.message,
						created_at:
							response.data.created_at || new Date().toString(),
					}

					setChats(prevChats => [...prevChats, assistantMessage])
				} else {
					console.error("Invalid response format:", response.data)
					throw new Error("Invalid response format from server")
				}
			} catch (err: any) {
				console.error("=== CHAT ERROR ===", err)
				toast.error(
					`Error: ${err.response?.data?.error || err.message}`,
				)

				// Remove the user message on error using the temp ID
				setChats(prevChats =>
					prevChats.filter(chat => chat._id !== tempUserId),
				)
			} finally {
				setIsLoading(false)
			}
		}, 500)

		setIsLoading(true)
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

			<div
				className={clsx(
					"relative py-4 w-full",
					isDragOver && "ring-2 ring-blue-500 ring-opacity-50",
				)}
				onDragEnter={handleDragEnter}
				onDragLeave={handleDragLeave}
				onDragOver={handleDragOver}
				onDrop={handleDrop}
			>
				{isDragOver && (
					<div className="z-10 absolute inset-0 flex justify-center items-center bg-blue-50 bg-opacity-90 border-2 border-blue-300 border-dashed rounded-lg">
						<div className="text-center">
							<BiImage className="mx-auto mb-2 text-blue-500 text-4xl" />
							<p className="font-medium text-blue-600">
								Drop image here
							</p>
						</div>
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
						disabled={
							isLoading ||
							isUploading ||
							(!message.length && !cloudinaryUrl)
						}
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
			</div>
		</>
	)
}

interface IInput {
	chats: Array<Chat>
	setChats: DispatchState<Array<Chat>>
	isLoading: boolean
	setIsLoading: DispatchState<boolean>
}
