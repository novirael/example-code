import { connect } from 'react-redux';
import { reduxForm, change } from 'redux-form';
import moment from 'moment';
import InvoiceForm from './InvoiceForm';

export const initialValuesItem = {
  item: null,
  pkwiu: '',
  single_price: 0,
  vat: '.23',
  quantity: 1,
  measure: 'szt',
  value_vat: 0,
};

const initialValuesFromUser = (currentUser) => ({
    who: currentUser.id,
    branch: currentUser.defaultBranch.id,
    date: moment().format('DD.MM.YYYY'),
    date_of_sale: moment().format('DD.MM.YYYY'),
    payment_methods: '0',
    payment_maturnity: '7',
    advance_payment: 0,
    items: [
      {...initialValuesItem},
    ]
});

const mapStateToProps = (state, ownProps) => ({
  branches: state.branchList.data,
  categories: state.saleCategoryList.data,
  users: state.userList.data,
  initialValues: ownProps.initialValues || initialValuesFromUser(state.currentUser),
});

const mapDispatchToProps = dispatch => ({
  changeField: (name, value) => dispatch(change('invoiceForm', name, value)),
});

const InvoiceFormConnected = reduxForm({form: 'invoiceForm'})(InvoiceForm);

export default connect(mapStateToProps, mapDispatchToProps)(InvoiceFormConnected);
