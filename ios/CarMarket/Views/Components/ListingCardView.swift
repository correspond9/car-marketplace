import SwiftUI

struct ListingCardView: View {
    let listing: Listing

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            if let url = listing.images.first?.url, let imageURL = URL(string: url) {
                AsyncImage(url: imageURL) { phase in
                    switch phase {
                    case .success(let image):
                        image.resizable().scaledToFill()
                    default:
                        Color.gray.opacity(0.2)
                    }
                }
                .frame(height: 180)
                .clipped()
            } else {
                Color.gray.opacity(0.15)
                    .frame(height: 180)
                    .overlay(Text("No photo").foregroundStyle(.secondary))
            }

            VStack(alignment: .leading, spacing: 6) {
                Text(title)
                    .font(.headline)
                Text("\(listing.manufacturingYear) · \(PriceFormatter.km(listing.odometerKm)) km · \(listing.city)")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Text(PriceFormatter.format(listing.askingPrice))
                    .font(.title3.bold())
                    .foregroundStyle(.green)
            }
            .padding(12)
        }
        .background(.background)
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .shadow(color: .black.opacity(0.06), radius: 4, y: 2)
    }

    private var title: String {
        var text = "\(listing.make) \(listing.model)"
        if let variant = listing.variant { text += " \(variant)" }
        return text
    }
}
