const initialState = {
    data: [],
    pagination: {
        currPage: 1,
        lastPage: 1,
        count: 0
    },
    fetched: false,
    error: null
};

export default function reducer(state=initialState, action) {

    switch (action.type) {
        case "FETCH_SALE_CATEGORY_LIST_REJECTED": {
            return { ...state, fetching: false, error: action.payload.detail }
        }
        case "FETCH_SALE_CATEGORY_LIST_FULFILLED": {
            return {
                ...state,
                fetched: true,
                data: action.payload.results,
                pagination: {
                    currPage: action.payload.curr_page,
                    lastPage: action.payload.last_page,
                    count: action.payload.count
                }
            }
        }
    }

    return state
}