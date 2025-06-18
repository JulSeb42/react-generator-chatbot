import { BASE_CLIENT_PATH, TEMPLATES_PATH } from "../utils/index.js"
import type { NodePlopAPI } from "plop"

export default (plop: NodePlopAPI) => {
    const { setGenerator } = plop

    setGenerator("page", {
        description: "",
        prompts: [],
        actions: [],
        // actions: data => {
        //     const actions = []
        //     return actions
        // },
    })
}
