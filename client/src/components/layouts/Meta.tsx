import { SITE_DATA } from "data"

export const Meta: FC<IMeta> = ({ title, description, keywords, cover }) => {
	return (
		<>
			<title>{`${title} | ${SITE_DATA.NAME}`}</title>
			<meta property="og:title" content={title} />
			<meta httpEquiv="Content-Type" content="text/html;charset=UTF-8" />
			<meta
				name="viewport"
				content="width=device-width, initial-scale=1.0"
			/>
			<meta name="referrer" content="origin" />
			<meta name="description" content={description} />
			<meta property="og:description" content={description} />
			<meta name="twitter:description" content={description} />
			<link
				rel="shortcut icon"
				href={SITE_DATA.FAVICON}
				type="image/x-icon"
			/>
			<link rel="icon" href={SITE_DATA.FAVICON} />
			<meta name="author" content={SITE_DATA.AUTHOR} />
			<meta name="creator" content={SITE_DATA.AUTHOR} />
			<meta name="twitter:creator" content={SITE_DATA.AUTHOR} />
			<meta
				name="keywords"
				content={[...SITE_DATA.KEYWORDS, keywords?.join(",")]?.join(
					",",
				)}
			/>
			<meta name="application-name" content={SITE_DATA.NAME} />
			<meta property="og:site_name" content={SITE_DATA.NAME} />
			<meta property="og:site_name" content={SITE_DATA.NAME} />
			<meta name="twitter:title" content={SITE_DATA.NAME} />
			<meta name="publisher" content={SITE_DATA.AUTHOR} />
			<meta name="category" content={SITE_DATA.TYPE} />
			<meta property="og:type" content={SITE_DATA.TYPE} />
			<meta property="og:image" content={cover} />
			<meta property="og:image" content={cover} />
			<meta name="twitter:image" content={cover} />
			<meta property="og:locale" content={SITE_DATA.LANGUAGE} />
			<meta property="og:url" content={SITE_DATA.URL} />
			<meta name="twitter:site" content={SITE_DATA.URL} />
			<meta property="og:email" content={SITE_DATA.EMAIL} />
			<meta name="twitter:card" content="summary" />
		</>
	)
}

export interface IMeta {
	title: string
	description?: string
	keywords?: Array<string>
	cover?: string
}
