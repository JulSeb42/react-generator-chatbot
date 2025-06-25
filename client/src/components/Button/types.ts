import type { ButtonHTMLAttributes } from "react"

export enum buttonVariant {
	primary,
	secondary,
}

export enum buttonColor {
	primary,
	danger,
}

export type ButtonVariant = keyof typeof buttonVariant
export type ButtonColor = keyof typeof buttonColor

export interface IButton extends ButtonHTMLAttributes<HTMLButtonElement> {
	variant?: ButtonVariant
	color?: ButtonColor
}
