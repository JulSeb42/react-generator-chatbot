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

			<section className="flex justify-center">
				<main className="flex flex-col gap-6 mx-auto py-12 w-full max-w-[800px] h-svh">
					{children}
				</main>
			</section>
		</>
	)
}

interface IPage extends IMeta {
	children?: Children
}
