import { connect } from 'react-redux';
import {fetchInvoice} from '../../actions/saleActions';
import InvoiceUpdate from './InvoiceUpdate';

const mapStateToProps = state => ({
    dataFetched: (
        state.userList.fetched &&
        state.branchList.fetched &&
        state.saleCategoryList.fetched &&
        state.saleInvoice.fetched
    ),
    invoiceData: state.saleInvoice.data,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
    updateInvoice: (values) => console.log(values),
    fetchInvoice: () => dispatch(fetchInvoice(ownProps.params.invoiceId)),
});

export default connect(mapStateToProps, mapDispatchToProps)(InvoiceUpdate);
