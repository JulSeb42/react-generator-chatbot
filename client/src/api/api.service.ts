import { http } from "./http-common"
import { BASE_API_URL } from "./server-paths"

class ApiService {
	hello() {
		return http.get(BASE_API_URL)
	}
}

export const apiService = new ApiService()
