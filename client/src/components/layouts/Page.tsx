import { Meta, type IMeta } from "./Meta"

export const Page: FC<IPage> = ({
	title,
	description,
	keywords,
	cover,
	children,
}) => {
	return (
		<>
			<Meta
				title={title}
				description={description}
				keywords={keywords}
				cover={cover}
			/>

			<section>
				<main>{children}</main>
			</section>
		</>
	)
}

interface IPage extends IMeta {
	children?: Children
}
