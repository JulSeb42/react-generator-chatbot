import type { ButtonHTMLAttributes } from "react";

export interface IButtonIcon extends ButtonHTMLAttributes<HTMLButtonElement> {
	icon: Children
	tooltip?: string
}
