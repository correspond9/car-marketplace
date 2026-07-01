import SwiftUI

struct LoginView: View {
    @StateObject private var viewModel = AuthViewModel()
    var onLoggedIn: () -> Void

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("CarMarket")
                    .font(.largeTitle.bold())
                Text("Sign in with your mobile number")
                    .foregroundStyle(.secondary)

                TextField("Mobile number", text: $viewModel.phone)
                    .keyboardType(.phonePad)
                    .textContentType(.telephoneNumber)
                    .padding()
                    .background(Color(.secondarySystemBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .disabled(viewModel.otpSent || viewModel.isLoading)

                if viewModel.otpSent {
                    TextField("OTP", text: $viewModel.otp)
                        .keyboardType(.numberPad)
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .clipShape(RoundedRectangle(cornerRadius: 10))
                    Text("Dev OTP: 123456")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                if let error = viewModel.errorMessage {
                    Text(error).foregroundStyle(.red).font(.footnote)
                }

                if viewModel.isLoading {
                    ProgressView()
                } else if viewModel.otpSent {
                    Button("Verify & continue") {
                        Task {
                            if await viewModel.verify() { onLoggedIn() }
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.green)
                } else {
                    Button("Send OTP") {
                        Task { await viewModel.sendOtp() }
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.green)
                }

                Spacer()
            }
            .padding(24)
        }
    }
}
