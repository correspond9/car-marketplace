import XCTest
@testable import CarMarket

final class CarMarketTests: XCTestCase {
    func testPriceFormatter() {
        let formatted = PriceFormatter.format(575000)
        XCTAssertTrue(formatted.contains("575") || formatted.contains("5,75,000"))
    }
}
