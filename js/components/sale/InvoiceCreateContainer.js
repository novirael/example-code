import { connect } from 'react-redux';

import InvoiceCreate from './InvoiceCreate';

const mapStateToProps = state => ({
    dataFetched: (
        state.currentUser.fetched &&
        state.userList.fetched &&
        state.branchList.fetched &&
        state.saleCategoryList.fetched
    ),
});

const mapDispatchToProps = dispatch => ({
    createInvoice: (values) => console.log(values),
});

export default connect(mapStateToProps, mapDispatchToProps)(InvoiceCreate);
