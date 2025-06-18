import type {
	FunctionComponent,
	ReactNode,
	Dispatch,
	SetStateAction,
	ElementType as ElType,
	ChangeEvent as ChangeE,
	FormEvent as FormE,
} from "react"

declare global {
	type FC<T> = FunctionComponent<T>
	type Children = ReactNode | Array<ReactNode>
	type DispatchState<T> = Dispatch<SetStateAction<T>>
	type ElementType = ElType
	type ChangeEvent<T> = ChangeE<T>
	type FormEvent = FormE<HTMLFormElement>
}
